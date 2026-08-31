from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4

from graph_builder import build_learning_graph
from explainer_agent import explain_with_llm
from nodes import get_shared_llm

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_learning_graph()

# Per-session replan counter. Not part of LangGraph state itself — derived
# by comparing current_index before/after each answer submission, since
# reflexion_node never advances current_index but advance_node always does.
replan_counts: dict[str, int] = {}


class StartRequest(BaseModel):
    goal: str
    background: str = ""


class AnswerRequest(BaseModel):
    answers: list[int]


class ExplainRequest(BaseModel):
    question: str


class AddResourceRequest(BaseModel):
    title: str
    url: str
    type: str = "custom"
    reason: str = "Added by learner"


def to_frontend_shape(session_id: str, state: dict, is_completed: bool = False) -> dict:
    """Translate backend LearningState into the shape frontend/src/api/client.js expects."""
    quiz_result = state.get("quiz_result") or {}
    return {
        "session_id": session_id,
        "user_id": state.get("user_id"),
        "current_index": state.get("current_index", 0),
        "is_completed": is_completed,
        "skill_gaps": (state.get("skill_gaps") or {}).get("skill_gaps", []),
        "learner_profile": state.get("learner_profile", {}),
        "mastery": state.get("mastery", {}),
        "current_path": state.get("current_path", []),
        "last_quiz": None if is_completed else state.get("last_quiz"),
        "last_quiz_score": quiz_result.get("score"),
        "is_passed": quiz_result.get("is_correct_overall"),
        "replan_count": replan_counts.get(session_id, 0),
        "explanation": (state.get("feedback") or {}).get("note") if not is_completed and replan_counts.get(session_id, 0) else None,
    }


@app.post("/session/start")
def start_session(req: StartRequest):
    session_id = str(uuid4())
    config = {"configurable": {"thread_id": session_id}}
    initial_state = {
        "user_id": session_id,
        "learner_profile": {
            "learning_goal": req.goal,
            "learner_information": req.background,
        },
        "mastery": {},
    }
    result = graph.invoke(initial_state, config=config, interrupt_before=["assessor"])
    return to_frontend_shape(session_id, result)


@app.post("/session/{session_id}/quiz/answer")
def submit_answer(session_id: str, req: AnswerRequest):
    config = {"configurable": {"thread_id": session_id}}

    prior_state = graph.get_state(config).values
    old_index = prior_state.get("current_index", 0)

    graph.update_state(config, {"submitted_answers": req.answers})
    result = graph.invoke(None, config=config, interrupt_before=["assessor"])

    new_index = result.get("current_index", 0)
    is_completed = new_index >= len(result.get("current_path", []))

    if new_index == old_index and not is_completed:
        replan_counts[session_id] = replan_counts.get(session_id, 0) + 1

    return to_frontend_shape(session_id, result, is_completed=is_completed)


@app.get("/session/{session_id}/state")
def get_state(session_id: str):
    config = {"configurable": {"thread_id": session_id}}
    result = graph.get_state(config).values
    is_completed = result.get("current_index", 0) >= len(result.get("current_path", []))
    return to_frontend_shape(session_id, result, is_completed=is_completed)


@app.get("/session/{session_id}/profile")
def get_profile(session_id: str):
    """Returns the explicit learner profile (interests, experience_level,
    completed_courses, objectives) built during intake."""
    config = {"configurable": {"thread_id": session_id}}
    state = graph.get_state(config).values

    if not state:
        raise HTTPException(status_code=404, detail="Session not found.")

    return state.get("learner_profile", {})


@app.post("/session/{session_id}/explain")
def explain_recommendation(session_id: str, req: ExplainRequest):
    """Answers a learner's free-text question about why the system
    recommended something, grounded in the session's current state."""
    config = {"configurable": {"thread_id": session_id}}
    state = graph.get_state(config).values

    if not state:
        raise HTTPException(status_code=404, detail="Session not found.")

    result = explain_with_llm(get_shared_llm(), req.question, state)
    return result


@app.post("/session/{session_id}/session/{session_index}/resource")
def add_resource(session_id: str, session_index: int, req: AddResourceRequest):
    """Add a custom resource link to a specific session in the active learning path."""
    config = {"configurable": {"thread_id": session_id}}
    state = graph.get_state(config).values

    if not state:
        raise HTTPException(status_code=404, detail="Session not found.")

    current_path = list(state.get("current_path", []))
    if session_index < 0 or session_index >= len(current_path):
        raise HTTPException(status_code=400, detail="Invalid session index.")

    target_session = dict(current_path[session_index])
    resources = list(target_session.get("recommended_resources", []))
    resources.append({
        "title": req.title,
        "url": req.url,
        "type": req.type,
        "reason": req.reason,
    })
    target_session["recommended_resources"] = resources
    current_path[session_index] = target_session

    graph.update_state(config, {"current_path": current_path})
    updated_state = graph.get_state(config).values
    is_completed = updated_state.get("current_index", 0) >= len(current_path)
    return to_frontend_shape(session_id, updated_state, is_completed=is_completed)


@app.get("/health")
def health():
    return {"status": "ok"}


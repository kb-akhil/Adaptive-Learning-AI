const BASE_URL = "http://localhost:8000";

function getToken() {
  return localStorage.getItem("token");
}

async function request(method, path, body = null) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export async function register(username, email, password) {
  const data = await request("POST", "/auth/register", { username, email, password });
  localStorage.setItem("token", data.access_token);
  localStorage.setItem("username", data.username);
  return data;
}

export async function login(username, password) {
  const data = await request("POST", "/auth/login", { username, password });
  localStorage.setItem("token", data.access_token);
  localStorage.setItem("username", data.username);
  return data;
}

export function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("username");
}

export async function getMe() {
  return request("GET", "/auth/me");
}

export async function uploadSyllabus(file) {
  const token = getToken();
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${BASE_URL}/upload/syllabus`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export async function getSyllabi() {
  return request("GET", "/upload/syllabi");
}

export async function generateAssessment(syllabusId) {
  return request("GET", `/assessment/generate/${syllabusId}`);
}

export async function submitAssessment(assessmentId, answers) {
  return request("POST", "/assessment/submit", {
    assessment_id: assessmentId,
    answers,
  });
}

export async function getAssessmentResult(assessmentId) {
  return request("GET", `/assessment/result/${assessmentId}`);
}

export async function getLatestLearningPath() {
  return request("GET", "/learning-path/latest/me");
}

export async function getLearningPath(assessmentId) {
  return request("GET", `/learning-path/${assessmentId}`);
}

export async function askTutor(question, topic = "", history = []) {
  return request("POST", "/tutor/ask", {
    question,
    topic,
    history,
  });
}
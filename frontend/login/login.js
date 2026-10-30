"use strict";

// 1. 실제 로그인 서비스가 구축되면 이 값에 Nginx의 로그인 API 경로를 지정한다.
// 예: const LOGIN_ENDPOINT = "/api/auth/login";
// 현재는 null이므로 실제 인증 없이 성공 처리하거나 임의 세션을 만들지 않는다.
const LOGIN_ENDPOINT = "http://localhost:8000/login/";

const form = document.querySelector("#loginForm");
const username = document.querySelector("#username");
const password = document.querySelector("#password");
const loginstatus = document.querySelector("#loginStatus");
const loginButton = document.querySelector("#loginButton");

// 2. 사용자가 비밀번호 입력 내용을 확인할 수 있도록 표시 상태만 변경한다.
document.querySelector("#togglePassword").addEventListener("click", (event) => {
    const visible = password.type === "text";
    password.type = visible ? "password" : "text";
    event.currentTarget.textContent = visible ? "보기" : "숨기기";
    event.currentTarget.setAttribute("aria-label", visible ? "비밀번호 표시" : "비밀번호 숨기기");
});

function showStatus(message, isError = false) {
    loginstatus.textContent = message; // 서버 문자열은 HTML로 해석하지 않는다.
    loginstatus.classList.toggle("error", isError);
    loginstatus.classList.add("show");
}

// 3. 로그인 버튼 처리: 유효성 검사 → 서버 요청 → 성공하면 채팅 페이지 이동.
// 서버의 인증 쿠키 설정은 FastAPI/Redis 세션 구성에서 담당한다.
form.addEventListener("submit", async (event) => {
    event.preventDefault(); // 브라우저 기본 form 제출로 새로고침하지 않는다.
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    if (!LOGIN_ENDPOINT) {
        showStatus("로그인 API가 아직 연결되지 않았습니다. FastAPI와 연결한 뒤 사용할 수 있어요.");
        return;
    }

    loginButton.disabled = true; // 중복 클릭으로 로그인 요청이 여러 번 가지 않게 한다.
    showStatus("로그인 요청을 확인하고 있어요.");
    try {
        const response = await fetch(LOGIN_ENDPOINT, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin", // Redis 세션 식별 쿠키를 받거나 전달하기 위한 옵션
            // 로그인 API가 form-data를 받는 설계라면 body 부분을 해당 형식으로 변경한다.
            body: JSON.stringify({ username: username.value.trim(), password: password.value })
        });
        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                showStatus("아이디 또는 비밀번호를 확인해 주세요.", true);
            } else {
                showStatus(`로그인 요청에 실패했습니다. (HTTP ${response.status})`, true);
            }
            return;
        }
        // 성공 여부는 서버의 HTTP 응답으로만 결정하며 프론트에서 인증 성공을 임의로 만들지 않는다.
        window.location.assign("chat.html");
    } catch (_) {
        showStatus("로그인 서버에 연결할 수 없습니다. 서버 실행 상태를 확인해 주세요.", true);
    } finally {
        loginButton.disabled = false;
    }
});
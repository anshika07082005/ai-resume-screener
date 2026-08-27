const API_BASE_URL = "http://127.0.0.1:8000";

let isLogin = true;


// ============================================================
// REDIRECT ALREADY LOGGED-IN USER
// ============================================================

document.addEventListener("DOMContentLoaded", () => {

  const token = localStorage.getItem("token");

  if (token && token !== "ok") {
    window.location.href = "index.html";
  }

});


// ============================================================
// TOGGLE LOGIN / REGISTER
// ============================================================

function toggleAuth() {

  isLogin = !isLogin;

  const title = document.getElementById("authTitle");
  const button = document.getElementById("authBtn");
  const switchText = document.getElementById("authSwitchText");
  const message = document.getElementById("authMessage");

  title.innerText =
    isLogin
      ? "Login"
      : "Register";

  button.innerText =
    isLogin
      ? "Login"
      : "Register";

  switchText.innerText =
    isLogin
      ? "Switch to Register"
      : "Switch to Login";

  message.innerText = "";
}


// ============================================================
// AUTHENTICATION
// ============================================================

async function handleAuth() {

  const email =
    document
      .getElementById("email")
      .value
      .trim();

  const password =
    document
      .getElementById("password")
      .value;

  const message =
    document.getElementById("authMessage");

  const button =
    document.getElementById("authBtn");


  message.innerText = "";


  if (!email || !password) {

    message.innerText =
      "Please enter email and password.";

    return;
  }


  if (!isLogin && password.length < 6) {

    message.innerText =
      "Password must contain at least 6 characters.";

    return;
  }


  const formData = new FormData();

  formData.append(
    "email",
    email
  );

  formData.append(
    "password",
    password
  );


  const endpoint =
    isLogin
      ? "/login"
      : "/register";


  try {

    button.disabled = true;

    button.innerText =
      isLogin
        ? "Logging in..."
        : "Registering...";


    const response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      {
        method: "POST",
        body: formData
      }
    );


    let data = {};

    try {
      data = await response.json();
    } catch {
      data = {};
    }


    if (!response.ok) {

      message.innerText =
        data.detail ||
        "Authentication failed.";

      return;
    }


    // ========================================================
    // LOGIN SUCCESS
    // ========================================================

    if (isLogin) {

      if (!data.access_token) {

        message.innerText =
          "Login succeeded but no access token was returned.";

        return;
      }


      localStorage.setItem(
        "token",
        data.access_token
      );


      if (data.user) {

        localStorage.setItem(
          "user",
          JSON.stringify(data.user)
        );

      }


      window.location.href =
        "index.html";

      return;
    }


    // ========================================================
    // REGISTER SUCCESS
    // ========================================================

    message.style.color = "#065f46";

    message.innerText =
      "Registration successful. Please log in.";


    setTimeout(() => {

      isLogin = true;

      document.getElementById(
        "authTitle"
      ).innerText = "Login";


      document.getElementById(
        "authBtn"
      ).innerText = "Login";


      document.getElementById(
        "authSwitchText"
      ).innerText =
        "Switch to Register";


      message.style.color = "";

      message.innerText =
        "Account created successfully. Log in to continue.";

    }, 700);


  } catch (error) {

    console.error(
      "Authentication error:",
      error
    );

    message.innerText =
      "Unable to connect to the backend. Make sure the server is running.";

  } finally {

    button.disabled = false;

    button.innerText =
      isLogin
        ? "Login"
        : "Register";

  }

}


// ============================================================
// ENTER KEY
// ============================================================

document.addEventListener(
  "keydown",
  event => {

    if (event.key === "Enter") {
      handleAuth();
    }

  }
);
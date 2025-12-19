let isLogin = true;

function toggleAuth() {
  isLogin = !isLogin;
  document.getElementById("authTitle").innerText =
    isLogin ? "Login" : "Register";
}

async function handleAuth() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const formData = new FormData();
  formData.append("email", email);
  formData.append("password", password);

  const endpoint = isLogin ? "login" : "register";

  const response = await fetch(`http://127.0.0.1:8000/${endpoint}`, {
    method: "POST",
    body: formData
  });

  const data = await response.json();

  if (response.ok) {
    localStorage.setItem("token", data.access_token || "ok");
    window.location.href = "index.html";
  } else {
    document.getElementById("authMessage").innerText =
      data.detail || "Authentication failed";
  }
}

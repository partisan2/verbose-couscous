<script>
    let email = "";
    let password = "";
    let error = "";

    async function login(){
        const res = await fetch("http://localhost:5000/auth/login",{
            method:"POST",
            headers:{"Content-Type": "application/json"},
            body: JSON.stringify({email,password})
        })

        const data = await res.json();

        if (data.token){
            localStorage.setItem("token",data.token)
            window.location.href ="#/chat";
        }else{
            error = "Inalid Login"
        }
    }
</script>

<h1>Login</h1>

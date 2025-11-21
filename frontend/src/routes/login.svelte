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

<div class=" w-full h-screen flex justify-center items-center bg-gray-200">
    <div class="flex flex-col gap-4 p-8 bg-white rounded shadow">
        {#if error}
            <p class="text-red-500">{error}</p>
        {/if}
        <h1 class="text-3xl text-blue-900">Login</h1>
        <input class="block border px-2 py-2 rounded" type="email" placeholder="Email" bind:value={email}>
        <input class="block border px-2 py-2 rounded" type="password" placeholder="Password" bind:value={password}>
        <button class="px-2 py-1 rounded text-white bg-blue-900 " on:click={login}>Login</button>
    </div>
    
</div>


<script>
    import { onMount } from "svelte";
    import { connectSocket } from "../lib/socket";

    let socket;
    let messages = [];
    let input = "";

    onMount(()=>{
        const token = localStorage.getItem("token");

        socket = connectSocket(token);

        socket.on("connect", ()=>{
            console.log("Connected to Server");
        })

        socket.on("message", (msg)=>{
            messages = [...messages, {from:"Assistant", text:msg}];
        })
    })

    function sendMsg() {
        messages = [...messages, { from: "Me", text: input }];
        socket.emit("message", input);
        input = "";
    }
</script>

<div class="w-full h-screen bg-gray-200 p-4">
    <h1 class="text-blue-900 text-3xl py-4">Chat Assistant</h1>
    
    <div class="border rounded w-full scroll-y-auto h-4/5 p-4 mb-16">
        {#each messages as m}
            <p><strong>{m.from}:</strong> {m.text}</p>
        {/each}
    </div>
    
    <div class="absolute bottom-5 w-full flex justify-center gap-4">
        <input class=" px-2 py-2 w-4/5 border-blue-600 border rounded" bind:value={input} placeholder="Type message..." />
        <button class="bg-blue-900 px-3 py-2 text-white rounded" on:click={sendMsg}>Send</button>
    </div>
</div>
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
            messages = [...messages, {from:"bot", text:msg}];
        })
    })

    function sendMsg() {
        messages = [...messages, { from: "me", text: input }];
        socket.emit("message", input);
        input = "";
    }
</script>

<h1>Chat</h1>

<div>
    {#each messages as m}
        <p><strong>{m.from}:</strong> {m.text}</p>
    {/each}
</div>

<input bind:value={input} placeholder="Type message..." />
<button on:click={sendMsg}>Send</button>
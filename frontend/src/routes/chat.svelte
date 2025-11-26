<script>
    import { onMount } from "svelte";
    import { connectSocket } from "../lib/socket";
    import { Icon } from 'svelte-icons-pack';
    import { BsSend } from "svelte-icons-pack/bs";

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

<div class="w-full h-screen bg-gray-200">
    <h1 class="text-blue-900 text-3xl p-4 ">Chat Assistant</h1>
    
    <div class="border rounded-2xl scroll-y-auto overflow-y-scroll h-4/5 mb-6 border-blue-400 mx-4 p-4 bg-white">
        {#each messages as m}
            {#if m.from === "Me"}
                <p class="text-right py-2">
                <strong class="text-green-800 block">{m.from}:</strong>
                    <span class="bg-green-500 px-4 py-1 rounded-2xl text-white border whitespace-pre-line">{m.text}</span>
                </p>
            {:else}
                <p class="text-left py-2 w-auto max-w-1/3"><strong class="text-blue-500 block">{m.from}:</strong> 
                    <span class="bg-blue-800 px-4 py-1 rounded-2xl text-white border whitespace-pre-line block leading-relaxed">
                        {m.text}
                    </span>
                </p>
            {/if}
        {/each}
    </div>
    
    <div class="absolute bottom-5 w-full flex justify-center mt-4 gap-4 px-4">
        <input class=" px-2 py-2 w-4/5 border-blue-300 focus:outline focus:outline-sky-500 border rounded bg-white" bind:value={input} placeholder="Type message..." />
        <button class="bg-blue-900 px-3 py-2 text-white rounded flex gap-2" on:click={sendMsg}>
            <span class="flex justify-center items-center px-2 py-1 gap-2">
                <Icon src={BsSend} size="1.5em" />
                Send
            </span>
        </button>
    </div>
</div>
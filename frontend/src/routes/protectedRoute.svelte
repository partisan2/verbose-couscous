<script>
    import Chat from "./chat.svelte";
    import navigate  from "svelte-spa-router";

    let token = localStorage.getItem("token");

    if (!token) {
        navigate("/login");
    }
</script>

{#if token}
    <Chat />
{/if}

<script>
  import Router from "svelte-spa-router";
  import Login from "./routes/login.svelte";
  import Chat from "./routes/chat.svelte";
  import ProtectedRoute from "./routes/protectedRoute.svelte";

  const routes = {
    "/":Login,
    "/login": Login,
    "/chat": ProtectedRoute
  };
</script>

<Router {routes} /> 

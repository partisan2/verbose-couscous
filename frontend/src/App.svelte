<script>
  import Router from "svelte-spa-router";
  import Login from "./routes/login.svelte";

  const routes = {
    "/":Login,
    "/login": Login,
  };
</script>

<Router {routes} /> 

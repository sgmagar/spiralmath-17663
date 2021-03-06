import React from "react";
import { Route, Switch } from "react-router-dom";
import { Container } from "react-bootstrap";

import PrivateRoute from "./components/private-route/private-route.component";
import SignUp from "./pages/signup/signup.component";
import Login from "./pages/login/login.component";
import ForgotPassword from "./pages/forgot-password/forgot-password.component";
import Dashboard from "./pages/dashboard/dashboard.component";
import Footer from "./components/footer/footer.component";

import "./App.css";

function App() {
  return (
    <Container>
      <Switch>
        <PrivateRoute path="/dashboard" exact component={Dashboard} />
        <Route path="/register" exact component={SignUp} />
        <Route path="/" exact component={Login} />
        <Route path="/forgot-password" exact component={ForgotPassword} />
      </Switch>

      <Footer />
    </Container>
  );
}

export default App;

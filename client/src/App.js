import React from 'react';
import {
    BrowserRouter as Router,
    Switch, Route
} from "react-router-dom";
import './App.css';
import Welcome from "./components/Welcome";
import Home from "./components/Home";

function App() {
  return (
      <Router>
        <div className="App">
            <Switch>
                <Route exact path="/">
                    <Welcome/>
                </Route>
                <Route exact path="/account">
                    <Home/>
                </Route>
            </Switch>
            
        </div>
      </Router>

  );
}

export default App;

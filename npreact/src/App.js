import "./App.css";
// importing components from react-router-dom package
import { Routes, Route } from 'react-router-dom';
import PDP from "./PDP";
import Register from "./Register";
import Login from "./Login";
import MP from "./MP";
import Search from "./Search";
import MDP from "./MDP";
 
function App() {
    return (
      <div className="App">
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/profile" element={<PDP />} />
        <Route path="/register" element={<Register />} />
        <Route path="/main" element={<MP />} />
        <Route path="/search/:movieName" element={<Search />} />
        <Route path="/rating/:movieName" element={<MDP />} />
      </Routes>
    </div>
    );
}
 
export default App;
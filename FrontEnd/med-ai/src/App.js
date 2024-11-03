import './App.css';
import Chatbot from './Components/Chatbot';
import Navbar from './Components/Navbar';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1 className="welcome-message">Welcome to Health-Scope!</h1>
        <Navbar />
      </header>
      <Chatbot />
    </div>
  );
}

export default App;

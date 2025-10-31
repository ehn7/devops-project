import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [tasks, setTasks] = useState([]);
  const [newTitle, setNewTitle] = useState("");

  // 1. Nossa função reutilizável para buscar tarefas
  const fetchTasks = () => {
    fetch('http://localhost:5000/api/tasks')
      .then(response => response.json())
      .then(data => {
        console.log("Dados da API recebidos:", data);
        setTasks(data); // Salva os dados no "estado"
      })
      .catch(error => {
        console.error("ERRO ao buscar dados da API:", error);
      });
  };

  // 2. Nosso useEffect, agora limpo, chamando a função
  useEffect(() => {
    fetchTasks(); // Busca as tarefas quando a página carrega
  }, []); // O [] vazio significa "rode apenas uma vez"

  // 3. Nossa função para Adicionar Tarefa (faz o POST)
  const handleAddTask = (event) => {
    event.preventDefault(); // Impede o reload
    
    const newTask = { title: newTitle };

    // Configura a requisição POST
    fetch('http://localhost:5000/api/tasks', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(newTask),
    })
    .then(response => response.json())
    .then(data => {
      console.log("Resposta do POST:", data.message);
      
      setNewTitle(""); // Limpa a caixa de texto
      
      // ATUALIZA A LISTA!
      fetchTasks(); // Busca a lista de tarefas novamente
    })
    .catch(error => {
      console.error("ERRO ao criar tarefa:", error);
    });
  };

  // 4. O HTML que será renderizado
  return (
    <div className="App">
      <header className="App-header">
        <h1>Minha Lista de Tarefas</h1>

        {/* Formulário para nova tarefa */}
        <form onSubmit={handleAddTask}>
          <input 
            type="text" 
            placeholder="Título da nova tarefa"
            value={newTitle} 
            onChange={ (e) => setNewTitle(e.target.value) } 
          />
          <button type="submit">Adicionar</button>
        </form>

        {/* Lista de tarefas */}
        {tasks.length === 0 ? (
          <p>Nenhuma tarefa encontrada.</p>
        ) : (
          <ul>
            {tasks.map(task => (
              <li key={task.id}>
                {task.title} (Status: {task.done ? "Concluída" : "Pendente"})
              </li>
            ))}
          </ul>
        )}
      </header>
    </div>
  );
}

export default App;
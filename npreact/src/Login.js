import './App.css';
import React from 'react';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { check_string, linkStyle, check_token_validity, get_token } from './imports';

const Login = () => {
    const navigate = useNavigate();
    const token = get_token();
    
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
  
    useEffect(() => {
      if ( token != undefined )
      { 
        check_token_validity(token)
        .then(result => {
          if ( result === 'valid' )
          {
              navigate('/main'); 
          }
        })
        .catch(error => {
          console.error(error);
        });
      }
    });

    async function login()
    {
        if ( check_string(email) || check_string(password) )
        {
            alert("EMPTY FIELD");
            return;
        }

        const payload = {
          'username':email,
          'password':password
        }

        try {
          const response = await fetch('http://localhost:8000/login/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
          });
    
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
    
          const responseData = await response.json();

          if ( responseData['token'] == "" )
              alert("Invalid Login!");
          else
          {
            let token = responseData['token'];
            document.cookie = `token=${token}; SameSite=None; Secure`;
            localStorage.setItem('token', token);
            window.location.replace('http://localhost:3000/main');
          }
        } catch (error) {
          alert(error.message);
        }
    }

    return (
      <div className="max-w-md mx-auto mt-8 p-6  rounded-md shadow-md text-left font-b">
        <h1 className="mt-32 text-5xl font-bold text-white">CRÉER UN COMPTE</h1>
        <form className="mt-8">
          <div className="mb-4">
            <label htmlFor="email" className="block text-white text-2xl font-bold mb-2"> Email </label>
            <input type="email" id="email" name="email" className="w-full bg-transparent text-white rounded-full border-2 border-cyan-500 p-2 focus:outline-none"
            onChange={event => setEmail(event.target.value)}
            value={email}/>
          </div>
  
          <div className="mb-4">
            <label htmlFor="password" className="block text-white text-2xl font-bold mb-2"> Mot de passe </label>
            <input type="password" id="password" name="password" className="w-full bg-transparent text-white rounded-full border-2 border-cyan-500 p-2 focus:outline-none"
            onChange={event => setPassword(event.target.value)}
            value={password}/>
          </div>
  
          <div className="mb-4">
          <h1 className="text-gray-500 text-xl">VOUS n'AVEZ pas DE COMPTE? <a className="text-cyan-300 text-xl" style={linkStyle} onClick={() => {navigate('/register');}}>INSCRIVEZ VOUS</a></h1>
          </div>
  
          <input className="w-full rounded-full bg-cyan-500 py-2 text-white hover:bg-cyan-600 transition duration-300 text-xl focus:outline-none" type="button" style={linkStyle}
          value="SE connecter" onClick={login}/>
          </form>
          </div>
    );
  };
  export default Login;
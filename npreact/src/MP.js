import React from 'react';
import { useState, useEffect } from 'react';
import { check_token_validity, get_token, linkStyle, clearCookies, disconnect } from './imports';
import { useNavigate } from 'react-router-dom';
import Loading from './Loading';

const MP = () => {
  const navigate = useNavigate();
  const token = get_token();

  const [forYou, setForYou] = useState([]);
  const [popular, setPopular] = useState([]);
  const [liked, setLiked] = useState([]);
  const [action, setAction] = useState([]);
  const [adventure, setAdventure] = useState([]);
  const [comedy, setComedy] = useState([]);
  const [thriller, setThriller] = useState([]);
  const [horror, setHorror] = useState([]);
  const [romance, setRomance] = useState([]);
  const [user, setUser] = useState([]);
  const [search, setSearch] = useState([]);
  const [loading, setLoading] = useState(true);

  const backdrop_path = popular.backdrop_path
    ? `https://image.tmdb.org/t/p/original/${popular.backdrop_path}`
    : 'https://cdn.gobankingrates.com/wp-content/uploads/2020/03/empty-movie-theater-shutterstock_257017468.jpg';

  const fetchOptions = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify({}),
  };

  useEffect(() => {
      check_token_validity(token)
      .then(result => {
        if ( token == undefined || result === 'expired' )
        {
            navigate('/');
            return;
        }
      })
      .catch(error => {
        console.error(error);
      });

      fetch(`http://localhost:8000/foryou/`, fetchOptions)
      .then((response) => response.json())
      .then((data) => setForYou(data));

      fetch(`http://localhost:8000/popular_movie/`)
      .then((response) => response.json())
      .then((data) => setPopular(data));

      fetch(`http://localhost:8000/liked/`, fetchOptions)
      .then((response) => response.json())
      .then((data) => setLiked(data));

      fetch(`http://localhost:8000/discover/?genre=Action`)
      .then((response) => response.json())
      .then((data) => setAction(data));

      fetch(`http://localhost:8000/discover/?genre=Adventure`)
      .then((response) => response.json())
      .then((data) => setAdventure(data));

      fetch(`http://localhost:8000/discover/?genre=Comedy`)
      .then((response) => response.json())
      .then((data) => setComedy(data));

      fetch(`http://localhost:8000/discover/?genre=Horror`)
      .then((response) => response.json())
      .then((data) => setHorror(data));

      fetch(`http://localhost:8000/discover/?genre=Thriller`)
      .then((response) => response.json())
      .then((data) => setThriller(data));

      fetch(`http://localhost:8000/discover/?genre=Romance`)
      .then((response) => response.json())
      .then((data) => setRomance(data));

      fetch(`http://localhost:8000/get_user/`, fetchOptions)
      .then((response) => response.json())
      .then((data) => setUser(data));
      
      
      const timeoutId = setTimeout(() => {
        // Your code to be executed after 2 seconds
        setLoading(false);
      }, 1500);
  
      // Clear the timeout if the component unmounts or if you want to cancel it for any reason
      return () => clearTimeout(timeoutId);

  }, []);

  const handleImageClick = (id) => {
    navigate(`/rating/${id}`)
  };

  const backgroundStyle = {
    backgroundImage: `url(${backdrop_path})`,
    backgroundSize: 'cover',
    backgroundPosition: 'top',
    minHeight: '700px',
  };

  const shadowBackgroundStyle = {
    background: 'linear-gradient(to right, rgba(0, 0, 0, 0.7) 30%, rgba(0, 0, 0, 0) 100%)', // Adjust color stops
    padding: '40px',
    borderRadius: '10px',
    minHeight: '700px',
  };

  if (loading) {
    // Display loading screen while data is being fetched
    return (
        <Loading />
    ); 
  }
    
  return (
    <div className="rounded-md shadow-md text-left font-b">
    <nav class="flex items-center justify-between flex-wrap p-6">
    <div class="flex items-center flex-shrink-0 text-white mr-6">
    <div> <img className='rounded-full w-12' src={require('./Image.jpeg')} alt ="PRP image" onClick={() => {navigate('/profile');}} style={linkStyle}/></div>
      <span class="ml-4 text-3xl tracking-tight max-sm:hidden lg:shown ">{user['username']}</span>
      <button className="max-sm:ml-4 ml-8 w-24 rounded-full border-2 border-cyan-700 p-1 text-cyan-500 hover:text-gray-300 hover:border-gray-300  transition duration-300 text-xl focus:outline-none" onClick={() => {disconnect();}}> DISCONNECT </button>
    </div>

    <div className="block text-center">
      <button
        className="text-white text-4xl font-bold cursor-pointer"
        style={{ fontSize: '2.5rem' }}  // Adjusted font size to 4xl
        onClick={() => { navigate('/'); }}
      >
        Miniflix
      </button>
    </div>

    <div class="block">
    <form onSubmit={(event) => {
        event.preventDefault();
        window.location.replace(`/search/${search}`);
      }}>
<label htmlFor="default-search" className="mb-2 text-sm font-medium text-gray-900 sr-only dark:text-white">
Search
</label>
<div className="relative">
<input
  type="search"
  id="default-search"
  className="lg:w-80 block max-sm:hidden w-full bg-transparent text-gray-700 focus:text-white rounded-full border-2 border-gray-700 p-2 focus:outline-none focus:border-cyan-300"
  placeholder="RECHERCHER"
  required
  onChange={(event) => setSearch(event.target.value)}
/>
<button type="submit" className="text-white absolute max-sm:bottom-0 end-3 bottom-3.5">
  <svg
    className="w-4 h-4 max-sm:w-6 max-sm:h-6 text-gray-500 dark:text-gray-400"
    aria-hidden="true"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 20 20"
  >
    <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z" />
  </svg>
</button>
</div>
</form>
    </div>
      </nav>

      <div className="mt-5" style={backgroundStyle}>

      <div> 

        <div style={shadowBackgroundStyle}>

          <div key={popular.id} className="movie-container">
            <div className="grid grid-cols-3 gap-8">
              <div>
                <h1 className="text-6xl mt-8 ml-20 text-white">{popular.title}</h1>
                <p className="text-2xl mt-4 ml-20 text-gray-300">{popular.overview}</p>
              </div>
            </div>
            
            <button className="ml-20 mt-16 w-60 rounded-full border-2 border-cyan-300 p-1 text-cyan-300 hover:text-gray-300 hover:border-gray-300  transition duration-300 text-xl focus:outline-none"
            onClick={() => {navigate(`/rating/${popular.title}`)}}> WATCH </button>
          
          </div>
          
        </div>
      
      </div>
    </div>
      
      <div className="mt-16">
        {forYou.length > 0 && (
          <>
            <h1 className="text-3xl mt-4 ml-10 text-white">POUR VOUS</h1>
            <div className="ml-8 mt-4 grid grid-cols-8 max-sm:grid-cols-2 max-md:grid-cols-4 max-lg:grid-cols-7 gap-3">
              {forYou.slice(0, 8).map((movie) => (
                <div key={movie.title} onClick={() => handleImageClick(movie.title)}>
                  <img
                    className="rounded-2xl hover:border-2 hover:border-gray-500 transition duration-300 w-full h-auto"
                    src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                    alt={movie.title}
                  />
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      <div className="mt-16">
      {
        Object.keys(liked).map((outerAttr, outerIndex) => (
          <div key={outerIndex}>
            <h1 className="text-3xl mt-4 ml-10 text-white">BECAUSE YOU LIKED {outerAttr}</h1>
            <div className="ml-8 mt-4 grid grid-cols-8 max-sm:grid-cols-2 max-md:grid-cols-4 max-lg:grid-cols-7 gap-3">
            
            {Object.keys(liked[outerAttr]).slice(0, 8).map((innerAttr, innerIndex) => (
              <div key={liked[outerAttr][innerAttr].title} onClick={() => handleImageClick(liked[outerAttr][innerAttr].title)}>
                <img className="rounded-2xl hover:border-2 hover:border-gray-500 transition duration-300 w-full h-auto" 
                src={`https://image.tmdb.org/t/p/w500${liked[outerAttr][innerAttr].poster_path}`} alt={liked[outerAttr][innerAttr].title}/>
            </div>
            
            ))}
          </div>
          </div>
        ))
      }
      </div>

      <div className="mt-16">
      <h1 className="text-3xl mt-4 ml-10 text-white">DISCOVER ACTION</h1>
      <div className="ml-8 mt-4 grid grid-cols-8 max-sm:grid-cols-2 max-md:grid-cols-4 max-lg:grid-cols-7 gap-3">

      {action.slice(0, 8).map((movie) => (
        <div key={movie.title} onClick={() => handleImageClick(movie.title)}>
            <img className="rounded-2xl hover:border-2 hover:border-gray-500 transition duration-300 w-full h-auto" src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title}/>
        </div>
      ))}
      </div>
      </div>

      <div className="mt-16">
      <h1 className="text-3xl mt-4 ml-10 text-white">DISCOVER ADVENTURE</h1>
      <div className="ml-8 mt-4 grid grid-cols-8 max-sm:grid-cols-2 max-md:grid-cols-4 max-lg:grid-cols-7 gap-3">

      {adventure.slice(0, 8).map((movie) => (
        <div key={movie.title} onClick={() => handleImageClick(movie.title)}>
            <img className="rounded-2xl hover:border-2 hover:border-gray-500 transition duration-300 w-full h-auto" src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title}/>
        </div>
      ))}
      </div>
      </div>

      <div className="mt-16">
      <h1 className="text-3xl mt-4 ml-10 text-white">DISCOVER COMEDY</h1>
      <div className="ml-8 mt-4 grid grid-cols-8 max-sm:grid-cols-2 max-md:grid-cols-4 max-lg:grid-cols-7 gap-3">

      {comedy.slice(0, 8).map((movie) => (
        <div key={movie.title} onClick={() => handleImageClick(movie.title)}>
            <img className="rounded-2xl hover:border-2 hover:border-gray-500 transition duration-300 w-full h-auto" src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title}/>
        </div>
      ))}
      </div>
      </div>

      <div className="mt-16">
      <h1 className="text-3xl mt-4 ml-10 text-white">DISCOVER HORROR</h1>
      <div className="ml-8 mt-4 grid grid-cols-8 max-sm:grid-cols-2 max-md:grid-cols-4 max-lg:grid-cols-7 gap-3">

      {horror.slice(0, 8).map((movie) => (
        <div key={movie.title} onClick={() => handleImageClick(movie.title)}>
            <img className="rounded-2xl hover:border-2 hover:border-gray-500 transition duration-300 w-full h-auto" src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title}/>
        </div>
      ))}
      </div>
      </div>

      <div className="mt-16">
      <h1 className="text-3xl mt-4 ml-10 text-white">DISCOVER THRILLER</h1>
      <div className="ml-8 mt-4 grid grid-cols-8 max-sm:grid-cols-2 max-md:grid-cols-4 max-lg:grid-cols-7 gap-3">

      {thriller.slice(0, 8).map((movie) => (
        <div key={movie.title} onClick={() => handleImageClick(movie.title)}>
            <img className="rounded-2xl hover:border-2 hover:border-gray-500 transition duration-300 w-full h-auto" src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title}/>
        </div>
      ))}
      </div>
      </div>

      <div className="mt-16">
      <h1 className="text-3xl mt-4 ml-10 text-white">DISCOVER ROMANCE</h1>
      <div className="ml-8 mt-4 grid grid-cols-8 max-sm:grid-cols-2 max-md:grid-cols-4 max-lg:grid-cols-7 gap-3">

      {romance.slice(0, 8).map((movie) => (
        <div key={movie.title} onClick={() => handleImageClick(movie.title)}>
            <img className="rounded-2xl hover:border-2 hover:border-gray-500 transition duration-300 w-full h-auto" src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title}/>
        </div>
      ))}
      </div>
      </div>

      </div>
    );
  };
  export default MP;
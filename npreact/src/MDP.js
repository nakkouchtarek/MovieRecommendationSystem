import React from 'react';
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { check_token_validity, get_token, linkStyle, clearCookies, disconnect } from './imports';
import Loading from './Loading';

const MDP = () => {
    const [movie, setMovie] = useState([]);
    const { movieName } = useParams();
    const [user, setUser] = useState([]);
    const [search, setSearch] = useState([]);
    const [selectedRating, setSelectedRating] = useState([]);
    const [movieID, setMovieID] = useState([]);
    const [loading, setLoading] = useState(true);

    const navigate = useNavigate();
    const token = get_token();

    const genreMapping = {
        28: 'Action',
        12: 'Adventure',
        16: 'Animation',
        35: 'Comedy',
        80: 'Crime',
        99: 'Documentary',
        18: 'Drama',
        10751: 'Family',
        14: 'Fantasy',
        36: 'History',
        27: 'Horror',
        10402: 'Music',
        9648: 'Mystery',
        10749: 'Romance',
        878: 'Science Fiction',
        10770: 'TV Movie',
        53: 'Thriller',
        10752: 'War',
        37: 'Western',
    };

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
      
      fetch(`http://localhost:8000/movie_details/?name=${movieName}`)
      .then((response) => response.json())
      .then((data) => {
        setMovie(data);
        setMovieID(data.myid);
      });       
      
      fetch(`http://localhost:8000/get_user/`, fetchOptions)
      .then((response) => response.json())
      .then((data) => setUser(data));

      const timeoutId = setTimeout(() => {
        // Your code to be executed after 2 seconds
        setLoading(false);
      }, 1000);
      
    }, []);

    const handleImageClick = (id) => {
      window.location.replace(`/rating/${id}`)
    };

    const handleRatingChange = (event) => {
      setSelectedRating(event.target.value);
    };

    const handleFormSubmit = (event) => {
      event.preventDefault();
      
      if (selectedRating) 
      {
        const payload = {
          'movieId': movieID,
          'rating': selectedRating,
        };
  
        fetchOptions.body = JSON.stringify(payload);

        fetch(`http://localhost:8000/rate_movie/`, fetchOptions)
        .then((response) => response.json())
        .then((data) => {
          if ( data.ok === 'ok' )
          {
            alert("Rated successfully!");
          }
        });
        }
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
        <div className="">
        <div>
          
          <div key={movie.id}>
          
          <div className="max-sm:pr-8 xl:mt-2 py-5 w-full h-full grid lg:grid-cols-3 gap-8">
          <div className="xl:ml-8 grid max-md:grid-cols-1 md:grid-cols-3 col-span-2 gap-0">
            <div className="col-span-1 max-md:px-16 max-sm:pb-8 mb-8 relative max-sm:mt-8 max-sm:bottom-0 ">
              <img className="lg:absolute lg:inset-y-0 lg:left-0 max-lg:hidden rounded-3xl w-auto blur-2xl" src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title}/>
              <img className="lg:absolute lg:inset-y-0 lg:left-0 hover:brightness-75 transition duration-300 rounded-3xl w-auto" src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title}/>
            </div>
              <div className="col-span-2">

              {movie.genres != undefined && movie.genres.map((element, index) => (
                  <button className="ml-8 w-24 rounded-full border-2 border-cyan-300 py-1 px-4 w-auto text-cyan-300 hover:text-gray-300 hover:border-gray-300  transition duration-300 text-xl focus:outline-none">{genreMapping[element]}</button>
              ))}

              <br />
              <h1 className="text-3xl mt-4 ml-10 text-gray-500">{movie.release_date}</h1>
              <h1 className="text-6xl mt-2 ml-10 text-white">{movie.title}</h1>
              <p className="text-2xl mt-4 ml-10 text-gray-300">{movie.overview}</p>

              <button className="ml-8 mt-8 w-64 max-sm:w-full rounded-full border-2 border-cyan-300 p-1 text-cyan-300 hover:text-gray-300 hover:border-gray-300  transition duration-300 text-xl focus:outline-none" type="button" onClick={() => {window.location.href=`https://www.youtube.com/embed/${movie.trailer}?autoplay=1'`;}}>WATCH</button>

            </div>
          </div>
          <div className="xl:mr-8 grid-cols-1 max-sm:lg-4 max-lg:px-8 col-span-1">
          <img className='w-10 max-sm:w-16' src={require('./star.png')}/>
          <h1 className="mt-2 max-lg:text-7xl text-5xl text-cyan-300">{movie.vote_average}</h1>
          <form onSubmit={handleFormSubmit}>
          <input className="hidden" name={movie.title} value={movie.id}/>
          <h1 className="mt-4 max-sm:pt-4 max-lg:text-4xl text-2xl text-white">Quelle note donnerer vous a ce film ?</h1>
          <ul className="mt-3 max-sm:py-4 max-md:w-auto grid max-lg:gap-20 gap-0 grid-cols-6">
        {[1, 2, 3, 4, 5].map((rating) => (
          <li key={rating}>
            <input
              type="radio"
              id={rating}
              name="rating"
              value={rating}
              className="bg-cyan-300 hidden peer"
              onChange={handleRatingChange}
              checked={selectedRating === `${rating}`}
            />
            <label
              htmlFor={rating}
              className="text-lg border-2 border-cyan-500 py-1 px-6 w-auto text-cyan-500 rounded-full hover:bg-cyan-500 hover:text-white peer-checked:bg-cyan-500 peer-checked:text-white transition duration-200 mr-2"
            >
              {rating}
            </label>
          </li>
        ))}
        <li>
          <input
            className="rounded-full py-0 px-3 border-2 border-cyan-500 text-cyan-500 rounded-full hover:bg-cyan-500 hover:text-white peer-checked:bg-cyan-500 peer-checked:text-white transition duration-200"
            type="submit"
            value="ENVOYER"
          />
        </li>
      </ul>
        </form>
          <h1 className="mt-6 max-lg:text-4xl text-2xl text-white">REGARDER LA BANDE ANNONCE</h1>
              <iframe className="mt-3 w-full aspect-video rounded-2xl hover:brightness-75 transition duration-300" src={`https://www.youtube.com/embed/${movie.trailer}`} allowfullscreen></iframe>
          </div>
          </div>
      <div>
    </div>
          </div>
          
          <br/><br/>
          <div className="px-12 pt-8 pb-8">
      
        <div className="px-12 pt-8 pb-8">
        <h1 className="text-3xl mt-4 text-white">FILMS SIMILAIRES</h1>
              <div className="mt-4 grid grid-cols-8 max-sm:grid-cols-2 max-md:grid-cols-4 max-lg:grid-cols-7 gap-3">
              {movie.recommendations != undefined && movie.recommendations.slice(0, 8).map((movie) => (
                <div key={movie.title}>
                    <img className="rounded-2xl hover:border-2 hover:border-gray-500 transition duration-300 w-full h-auto" src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title} onClick={() => handleImageClick(movie.title)}/>
                </div>
        ))}
              </div>
              </div>
      </div>
  </div>
        
      
      </div>
      </div>
      );
    };
  
    export default MDP;
        
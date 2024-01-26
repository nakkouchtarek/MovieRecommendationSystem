// content.js
function isCodeLike(text) {
  // Add more sophisticated logic as needed to identify code-like patterns
  // Here, we are using a simple check for the presence of common code-related keywords
  const codeKeywords = ['function', 'var', 'const', 'let', 'if', 'else', '{', '}', '=>'];
  return codeKeywords.some(keyword => text.includes(keyword));
}

function scrapeTag(tag) {
  const elements = document.querySelectorAll(tag);
  return Array.from(elements)
    .filter(elem => elem.textContent.trim() !== '' && !isCodeLike(elem.textContent))
    .map(elem => elem.textContent.trim());
}

const tagsToScrape = ["h1", "h2", "h3", "h4", "h5", "h6", "span", "textarea", "a", "div"];

const scrapedData = {
  results: tagsToScrape.reduce((result, tag) => {
    const data = scrapeTag(tag);
    return result.concat(data);
  }, [])
};


const apiUrl = 'http://localhost:8000/extension/';  // Replace with your API endpoint

const currentUrl = window.location.href;

if ( currentUrl.includes("localhost") )
{
  chrome.storage.sync.set({ 'token': localStorage.getItem('token') }, function() {
    if (chrome.runtime.lastError) {
      console.error('Error storing token:', chrome.runtime.lastError);
    } else {
      console.log(`Token stored: ${localStorage.getItem('token')}`);
    }
  });
}
else
{
  chrome.storage.sync.get(['token'], function(result) {
    console.log(`This is token: ${result.token}`);
    if(result.token != undefined) 
    {
      fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${result.token}`
        },
        body: JSON.stringify(scrapedData),
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Data sent successfully:', data);
      })
      .catch(error => {
        console.error('Error sending data:', error);
      });
    }
  });
}

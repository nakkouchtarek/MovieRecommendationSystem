export async function check_token_validity(token)
{
  const payload = {
    'token': token,
  };

  try {
    const response = await fetch('http://localhost:8000/check_validity/', {
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
    return responseData['state'];

  } catch (error) {
    return 'expired';
  }
};

export function get_token()
{
  return document.cookie.split('; ').filter(row => row.startsWith('token=')).map(c=>c.split('=')[1])[0];
}

export function check_string(string)
{
    return string === '';
}

export const linkStyle = {cursor: 'pointer'};

export function clearCookies() {
  // Get all cookies
  const cookies = document.cookie.split(';');

  // Iterate through cookies and set each one to expire in the past
  cookies.forEach(cookie => {
    const [name, _] = cookie.split('=');
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
  });
}

export function disconnect()
{
  clearCookies();
  localStorage.removeItem('token');
  window.location.replace('http://localhost:3000/');
} 
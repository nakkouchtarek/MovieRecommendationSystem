import React from 'react';

class Loading extends React.Component {
  render() {
    return (
      <html lang="en">
        <head>
          <meta charSet="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>Loading Page</title>
          <style>
            {`
              body {
                margin: 0;
                padding: 0;
                background-color: #000;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
              }

              .loader {
                border: 8px solid cyan;
                border-top: 8px solid transparent;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
              }

              @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
              }
            `}
          </style>
        </head>
        <body>
          <div className="loader"></div>
        </body>
      </html>
    );
  }
}

export default Loading;

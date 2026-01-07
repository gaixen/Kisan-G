# Project Description

Farmers today face a multitude of challenges. Access to timely and accurate information regarding crop
diseases, market prices, government support systems, and environmental conditions is often fragmented and
difficult to obtain. This information gap can lead to reduced yields, financial losses, and an inability
to take advantage of available resources. Kisan-G aims to bridge this gap by providing a one-stop
solution that is both powerful and easy to use.

# Solution

Kisan-G is a multi-faceted web application(extendable to modile as well) designed to empower farmers by providing them with advanced
tools and timely information to improve crop yield, increase profitability, and make informed decisions.
Leveraging a sophisticated backend powered by AI and web scraping, and a user-friendly frontend built with
React, Agri-Assist integrates several critical services into a single, accessible platform. The key
features include an AI-powered "Crop Doctor" for disease diagnosis, a "Market Analyst" for real-time price
trends, a "Scheme Navigator" for accessing information on government agricultural schemes, and a "Soil
and Weather" analysis module for precision farming.

# Running Instructions

- clone the repo using the command

```bash
git clone https://github.com/gaixen/Kisan-G.git kisan-g
```

- change the working directory using :

```bash
cd ./kisan-g
```

- add a .env file in the root directory with the following content

```
GEMINI_API_KEY = ""
TAVILY_API_KEY = ""
GOOGLE_APPLICATION_CREDENTIALS = /*path of json file from console.cloud.google.com*/
```

- Install the dependencies using the command

```bash
python -m pip install -r requirements.txt
```

- run this command to get the react dependencies

```bash
npm install
```

open the project directory and run the command

```bash
npm start
```

- This will execute the frontend of the application

Next change the working directory to ./server

```bash
cd ./server
```

```bash
python app.py
```

- This will connect the backend server to the frontend

# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)

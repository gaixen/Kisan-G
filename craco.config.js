// craco config json
module.exports = {
    devserver: {
        setupMiddleware: (middlewares, devserver) => {
            if (!devserver){
                throw new Error('webpack-dev-server not defined!');
            }
            return middlewares;
        }
    }
}
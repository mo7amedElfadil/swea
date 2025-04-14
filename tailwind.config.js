/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ['./app/templates/**/*.html', './app/static/js/*.js'],
    theme: {
        extend: {
            gridTemplateColumns: {
                fluid: 'repeat(auto-fit, minmax(300px, 450px))',
            },
            backgroundSize: {
                900: '900px', // Add your custom size here
            },
            colors: {
                primary: {
                    50: '#ffefef',
                    100: '#ffdcdc',
                    200: '#ffbfbf',
                    300: '#ff9292',
                    400: '#ff5454',
                    500: '#ff1f1f',
                    600: '#ff0000',
                    700: '#db0000',
                    800: '#b80000',
                    900: '#940808',
                    950: '#520000',
                },
                secondary: {
                    50: '#fcf6f0',
                    100: '#F6E5D3',
                    200: '#f0d3b8',
                    300: '#e6b48b',
                    400: '#db8e5c',
                    500: '#d2713d',
                    600: '#c45c32',
                    700: '#a3472b',
                    800: '#833b29',
                    900: '#6a3224',
                    950: '#391811',
                },
            },
            fontFamily: {
                primary: ['"Noto Kufi Arabic"', 'serif'],
                secondary: ['sans-serif'],
            },
            animation: {
                'spin-slow': 'spin 1.5s linear infinite',
                'fade-in': 'fadeIn 0.4s ease-in-out',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: 0 },
                    '100%': { opacity: 1 },
                },
            },
        },
    },
    plugins: [],
}

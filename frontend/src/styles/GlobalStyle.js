import { createGlobalStyle } from 'styled-components';

export const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  html {
    font-size: 16px;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  body {
    font-family: ${props => props.theme?.typography?.fontFamily || "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif"};
    background: ${props => props.theme?.colors?.background || '#0F172A'};
    color: ${props => props.theme?.colors?.text || '#F1F5F9'};
    line-height: ${props => props.theme?.typography?.lineHeight?.normal || 1.5};
    overflow-x: hidden;
  }

  code {
    font-family: 'Fira Code', 'Courier New', monospace;
  }

  a {
    color: inherit;
    text-decoration: none;
  }

  button {
    cursor: pointer;
    border: none;
    outline: none;
    font-family: inherit;
    background: transparent;
  }

  input, select, textarea {
    font-family: inherit;
    outline: none;
  }

  h1, h2, h3, h4, h5, h6 {
    font-weight: ${props => props.theme?.typography?.fontWeight?.bold || 700};
    line-height: ${props => props.theme?.typography?.lineHeight?.tight || 1.25};
    color: ${props => props.theme?.colors?.text || '#F1F5F9'};
  }

  p {
    line-height: ${props => props.theme?.typography?.lineHeight?.normal || 1.5};
  }

  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
  
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }

  /* Smooth scrolling */
  html {
    scroll-behavior: smooth;
  }

  /* Selection styling */
  ::selection {
    background: ${props => props.theme?.colors?.primaryGlow || 'rgba(6, 182, 212, 0.3)'};
    color: ${props => props.theme?.colors?.text || '#F1F5F9'};
  }
`;
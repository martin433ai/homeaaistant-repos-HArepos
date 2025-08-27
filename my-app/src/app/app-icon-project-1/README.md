# App Icon Project

This project is designed to create and manage an app icon using React and TypeScript. It includes an SVG representation of the icon, a functional component to render the icon, and modular CSS for styling.

## Project Structure

```
app-icon-project
├── src
│   ├── assets
│   │   └── icon.svg          # SVG representation of the app icon
│   ├── components
│   │   └── Icon.tsx          # React component for rendering the icon
│   └── styles
│       └── Icon.module.css    # CSS styles for the Icon component
├── package.json               # npm configuration file
├── tsconfig.json              # TypeScript configuration file
└── README.md                  # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd app-icon-project
   ```

2. Install dependencies:
   ```
   npm install
   ```

## Usage

To use the Icon component in your application, import it as follows:

```tsx
import Icon from './components/Icon';

function App() {
  return (
    <div>
      <Icon size={50} color="blue" />
    </div>
  );
}
```

## Customization

The `Icon` component accepts the following props for customization:

- `size`: Specifies the size of the icon (default is 24).
- `color`: Specifies the color of the icon (default is black).

## License

This project is licensed under the MIT License.
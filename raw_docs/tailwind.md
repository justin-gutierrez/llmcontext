# Tailwind CSS Documentation

## Introduction

Tailwind CSS is a utility-first CSS framework that allows you to build custom designs without leaving your HTML. It provides low-level utility classes that let you build completely custom designs without ever leaving your HTML.

## Installation

### Using npm

```bash
npm install -D tailwindcss
npx tailwindcss init
```

### Using CDN

```html
<script src="https://cdn.tailwindcss.com"></script>
```

## Configuration

Create a `tailwind.config.js` file in your project root:

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./pages/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#10B981',
      },
      spacing: {
        '128': '32rem',
      },
    },
  },
  plugins: [],
}
```

## Basic Usage

### Utility Classes

Tailwind provides utility classes for common CSS properties:

```html
<!-- Spacing -->
<div class="p-4 m-2">Padding and margin</div>

<!-- Colors -->
<div class="bg-blue-500 text-white">Blue background with white text</div>

<!-- Typography -->
<h1 class="text-2xl font-bold text-gray-900">Large bold heading</h1>

<!-- Layout -->
<div class="flex items-center justify-between">
  <span>Left content</span>
  <span>Right content</span>
</div>
```

### Responsive Design

Use responsive prefixes to apply styles at different breakpoints:

```html
<div class="w-full md:w-1/2 lg:w-1/3">
  <!-- Full width on mobile, half on medium, third on large -->
</div>
```

### Hover and Focus States

```html
<button class="bg-blue-500 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50">
  Interactive button
</button>
```

## Common Patterns

### Card Component

```html
<div class="max-w-sm rounded overflow-hidden shadow-lg">
  <img class="w-full" src="image.jpg" alt="Card image">
  <div class="px-6 py-4">
    <div class="font-bold text-xl mb-2">Card Title</div>
    <p class="text-gray-700 text-base">
      Card description text goes here.
    </p>
  </div>
  <div class="px-6 pt-4 pb-2">
    <span class="inline-block bg-gray-200 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 mr-2">#tag1</span>
    <span class="inline-block bg-gray-200 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 mr-2">#tag2</span>
  </div>
</div>
```

### Navigation Bar

```html
<nav class="bg-gray-800">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex items-center justify-between h-16">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <img class="h-8 w-8" src="logo.svg" alt="Logo">
        </div>
        <div class="hidden md:block">
          <div class="ml-10 flex items-baseline space-x-4">
            <a href="#" class="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">Home</a>
            <a href="#" class="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">About</a>
            <a href="#" class="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">Contact</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</nav>
```

## Customization

### Extending the Theme

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'brand': {
          50: '#f0f9ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        }
      },
      fontFamily: {
        'sans': ['Inter', 'sans-serif'],
      },
      spacing: {
        '18': '4.5rem',
      }
    }
  }
}
```

### Custom Utilities

```css
@layer utilities {
  .text-shadow {
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .text-shadow-lg {
    text-shadow: 4px 4px 8px rgba(0, 0, 0, 0.15);
  }
}
```

## Best Practices

1. **Use semantic class names**: Group related utilities together
2. **Leverage responsive design**: Use responsive prefixes for mobile-first design
3. **Extract components**: Use @apply for repeated patterns
4. **Optimize for production**: Use PurgeCSS to remove unused styles

## Common Issues

### Class Conflicts

If you have conflicting classes, the last one in the HTML wins:

```html
<!-- This will be red, not blue -->
<div class="text-blue-500 text-red-500">Red text</div>
```

### Specificity Issues

Tailwind uses a specific order for utilities. If you need higher specificity:

```css
@layer components {
  .my-custom-button {
    @apply bg-blue-500 text-white px-4 py-2 rounded;
  }
}
```

### Build Performance

For large projects, consider:

- Using JIT mode for faster builds
- Configuring content paths properly
- Using CDN for development only 
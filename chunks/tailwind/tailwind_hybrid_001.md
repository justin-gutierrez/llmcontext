# tailwind_hybrid_001

**Metadata:** {'strategy': 'hybrid', 'header_level': 2, 'line_count': 77, 'document_id': 'tailwind'}

**Tokens:** 935-1353

---

-2 rounded-md text-sm font-medium">Home</a>
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
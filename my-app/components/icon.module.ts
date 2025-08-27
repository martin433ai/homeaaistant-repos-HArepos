import React from 'react';

// Icon Properties Interface
export interface IconProps {
  name: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | number;
  color?: string;
  className?: string;
  style?: React.CSSProperties;
  rotate?: number; // rotation in degrees
  flip?: 'horizontal' | 'vertical' | 'both';
  spin?: boolean;
  pulse?: boolean;
  onClick?: () => void;
}

// Icon Size Configuration
export const IconSizes = {
  xs: 12,
  sm: 16,
  md: 24,
  lg: 32,
  xl: 48,
};

// Default Icon Configuration
export const DefaultIconConfig = {
  size: 'md' as const,
  color: 'currentColor',
  rotate: 0,
  flip: undefined as undefined | 'horizontal' | 'vertical' | 'both',
  spin: false,
  pulse: false,
};

// Icon Utility Functions
export class IconUtils {
  /**
   * Get the numeric size value from either a predefined size or a custom number
   */
  static getSize(size: IconProps['size']): number {
    if (typeof size === 'number') {
      return size;
    }
    
    return size ? IconSizes[size] : IconSizes[DefaultIconConfig.size];
  }

  /**
   * Generate style object based on icon properties
   */
  static getStyleFromProps(props: IconProps): React.CSSProperties {
    const {
      size = DefaultIconConfig.size,
      color = DefaultIconConfig.color,
      rotate = DefaultIconConfig.rotate,
      flip = DefaultIconConfig.flip,
      spin = DefaultIconConfig.spin,
      pulse = DefaultIconConfig.pulse,
      style = {},
    } = props;

    const sizeValue = this.getSize(size);

    const baseStyle: React.CSSProperties = {
      width: sizeValue,
      height: sizeValue,
      color,
      display: 'inline-block',
      ...style,
    };

    // Apply transformations
    const transforms: string[] = [];
    
    if (rotate) {
      transforms.push(`rotate(${rotate}deg)`);
    }
    
    if (flip) {
      switch (flip) {
        case 'horizontal':
          transforms.push('scaleX(-1)');
          break;
        case 'vertical':
          transforms.push('scaleY(-1)');
          break;
        case 'both':
          transforms.push('scale(-1)');
          break;
      }
    }
    
    if (transforms.length > 0) {
      baseStyle.transform = transforms.join(' ');
    }
    
    // Apply animations
    if (spin || pulse) {
      baseStyle.animation = spin 
        ? 'spin 2s infinite linear' 
        : 'pulse 2s infinite ease-in-out';
    }

    return baseStyle;
  }

  /**
   * Apply color to an SVG string
   */
  static colorize(svgString: string, color: string): string {
    // A simple implementation to replace fill attributes
    // More complex implementations might use a DOM parser
    return svgString.replace(/fill="[^"]*"/g, `fill="${color}"`);
  }

  /**
   * Create animation styles for spin and pulse effects
   */
  static getAnimationStyles(): string {
    return `
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      
      @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
      }
    `;
  }
}

// Type for icon registry
export interface IconRegistry {
  [key: string]: string; // Maps icon name to SVG string
}

// Icon registry for storing SVG strings
export class IconRegistryService {
  private static registry: IconRegistry = {};

  /**
   * Register a new icon
   */
  static register(name: string, svgString: string): void {
    this.registry[name] = svgString;
  }

  /**
   * Register multiple icons at once
   */
  static registerBulk(icons: IconRegistry): void {
    Object.entries(icons).forEach(([name, svg]) => {
      this.register(name, svg);
    });
  }

  /**
   * Get an icon by name
   */
  static getIcon(name: string): string | undefined {
    return this.registry[name];
  }

  /**
   * Check if an icon exists
   */
  static hasIcon(name: string): boolean {
    return name in this.registry;
  }

  /**
   * Remove an icon from the registry
   */
  static unregister(name: string): void {
    delete this.registry[name];
  }

  /**
   * Clear the entire registry
   */
  static clear(): void {
    this.registry = {};
  }
}

const IconModule = {
  IconSizes,
  DefaultIconConfig,
  IconUtils,
  IconRegistryService
};

export default IconModule;

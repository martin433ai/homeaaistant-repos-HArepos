import React from 'react';
import styles from '../styles/Icon.module.css';
import IconSVG from '../assets/icon.svg';

interface IconProps {
  size?: number;
  color?: string;
}

const Icon: React.FC<IconProps> = ({ size = 24, color = 'currentColor' }) => {
  return (
    <img
      src={IconSVG}
      alt="App Icon"
      className={styles.icon}
      style={{ width: size, height: size, fill: color }}
    />
  );
};

export default Icon;
import * as React from "react";
import styles from "../styles/Icon.module.css";

interface IconProps {
  size: number;
  color: string;
  flag?: boolean;
}

export const Icon: React.FC<IconProps> = ({ size, color, flag = false }) => {
  return (
    <div
      className={styles.icon}
      style={{
        width: `${size}px`,
        height: `${size}px`,
        backgroundColor: color,
        border: flag ? "2px solid black" : "none",
      }}
    >
      {/* Icon content can be customized further as needed */}
    </div>
  );
};

export default Icon;

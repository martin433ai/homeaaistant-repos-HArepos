import * as React from "react";
import { Icon } from "./Icon";

interface AppletIconProps {
  size?: number;
  color?: string;
  showFlag?: boolean;
}

export const AppletIcon: React.FC<AppletIconProps> = ({
  size = 48,
  color = "#3498db",
  showFlag = false,
}) => {
  return (
    <div className="applet-icon-wrapper">
      <Icon size={size} color={color} flag={showFlag} />
    </div>
  );
};

export default AppletIcon;

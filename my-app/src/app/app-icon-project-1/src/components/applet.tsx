import React from "react";
import { scaleLinear } from "d3-scale";
import Icon from "./Icon";

// Example usage of d3-scale
const scale = scaleLinear().domain([0, 100]).range([0, 1]);

console.log(scale(50)); // Output: 0.5

const App = () => {
  return (
    <div>
      <Icon size={48} color="red" flag={true} />
    </div>
  );
};

export default App;

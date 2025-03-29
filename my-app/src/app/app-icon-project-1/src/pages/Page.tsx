import Image from "next/image";
import * as React from "react";

export default function Page() {
  return (
    <Image
      src="/profile.png"
      width={500}
      height={500}
      alt="Picture of the author"
      fill
    />
  );
}

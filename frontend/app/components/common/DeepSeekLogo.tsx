'use client';

import Image from 'next/image';

interface DeepSeekLogoProps {
  size?: number;
  className?: string;
}

export default function DeepSeekLogo({ size = 20, className = '' }: DeepSeekLogoProps) {
  return (
    <Image 
      src="/deepseek_logo.png" 
      alt="DeepSeek Logo" 
      width={size} 
      height={size}
      className={className}
    />
  );
}


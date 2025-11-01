'use client';

interface CoinIconProps {
  symbol: string;
  size?: number;
  className?: string;
}

export default function CoinIcon({ symbol, size = 20, className = '' }: CoinIconProps) {
  // 提取币种名称（去掉-PERP等后缀）
  const coinName = symbol.replace('-PERP', '').replace('!', '').toLowerCase();
  
  const svgStyle = { width: `${size}px`, height: `${size}px`, display: 'inline-block' };

  // 直接返回内嵌SVG
  switch (coinName) {
    case 'btc':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4091.27 4091.73" style={svgStyle} className={className}>
          <path fill="#F7931A" d="M4030.06 2540.77c-273.24,1096.01 -1383.32,1763.02 -2479.46,1489.71 -1095.68,-273.24 -1762.69,-1383.39 -1489.33,-2479.31 273.12,-1096.13 1383.2,-1763.19 2479,-1489.95 1096.06,273.24 1763.03,1383.51 1489.76,2479.57l0.02 -0.02z"/>
          <path fill="white" d="M2947.77 1754.38c40.72,-272.26 -166.56,-418.61 -450,-516.24l91.95 -368.8 -224.5 -55.94 -89.51 359.09c-59.02,-14.72 -119.63,-28.59 -179.87,-42.34l90.16 -361.46 -224.36 -55.94 -92 368.68c-48.84,-11.12 -96.81,-22.11 -143.35,-33.69l0.26 -1.16 -309.59 -77.31 -59.72 239.78c0,0 166.56,38.18 163.05,40.53 90.91,22.69 107.35,82.87 104.62,130.57l-104.74 420.15c6.26,1.59 14.38,3.89 23.34,7.49 -7.49,-1.86 -15.46,-3.89 -23.73,-5.87l-146.81 588.57c-11.11,27.62 -39.31,69.07 -102.87,53.33 2.25,3.26 -163.17,-40.72 -163.17,-40.72l-111.46 256.98 292.15 72.83c54.35,13.63 107.61,27.89 160.06,41.3l-92.9 373.03 224.24 55.94 92 -369.07c61.26,16.63 120.71,31.97 178.91,46.43l-91.69 367.33 224.51 55.94 92.89 -372.33c382.82,72.45 670.67,43.24 791.83,-303.02 97.63,-278.78 -4.86,-439.58 -206.26,-544.44 146.69,-33.83 257.18,-130.31 286.64,-329.61l-0.07 -0.05zm-512.93 719.26c-69.38,278.78 -538.76,128.08 -690.94,90.29l123.28 -494.2c152.17,37.99 640.17,113.17 567.67,403.91zm69.43 -723.3c-63.29,253.58 -453.96,124.75 -580.69,93.16l111.77 -448.21c126.73,31.59 534.85,90.55 468.94,355.05l-0.02 0z"/>
        </svg>
      );
    case 'eth':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 784.37 1277.39" style={svgStyle} className={className}>
          <polygon fill="#343434" points="392.07,0 383.5,29.11 383.5,873.74 392.07,882.29 784.13,650.54"/>
          <polygon fill="#8C8C8C" points="392.07,0 0,650.54 392.07,882.29 392.07,472.33"/>
          <polygon fill="#3C3C3B" points="392.07,956.52 387.24,962.41 387.24,1263.28 392.07,1277.38 784.37,724.89"/>
          <polygon fill="#8C8C8C" points="392.07,1277.38 392.07,956.52 0,724.89"/>
          <polygon fill="#141414" points="392.07,882.29 784.13,650.54 392.07,472.33"/>
          <polygon fill="#393939" points="0,650.54 392.07,882.29 392.07,472.33"/>
        </svg>
      );
    case 'sol':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 397.7 311.7" style={svgStyle} className={className}>
          <defs>
            <linearGradient id="solGrad1" x1="360.88" y1="351.46" x2="141.21" y2="-69.29" gradientTransform="matrix(1 0 0 -1 0 314)" gradientUnits="userSpaceOnUse">
              <stop offset="0" stopColor="#00FFA3"/>
              <stop offset="1" stopColor="#DC1FFF"/>
            </linearGradient>
            <linearGradient id="solGrad2" x1="264.83" y1="401.6" x2="45.16" y2="-19.15" gradientTransform="matrix(1 0 0 -1 0 314)" gradientUnits="userSpaceOnUse">
              <stop offset="0" stopColor="#00FFA3"/>
              <stop offset="1" stopColor="#DC1FFF"/>
            </linearGradient>
            <linearGradient id="solGrad3" x1="312.55" y1="376.69" x2="92.88" y2="-44.06" gradientTransform="matrix(1 0 0 -1 0 314)" gradientUnits="userSpaceOnUse">
              <stop offset="0" stopColor="#00FFA3"/>
              <stop offset="1" stopColor="#DC1FFF"/>
            </linearGradient>
          </defs>
          <path fill="url(#solGrad1)" d="M64.6,237.9c2.4-2.4,5.7-3.8,9.2-3.8h317.4c5.8,0,8.7,7,4.6,11.1l-62.7,62.7c-2.4,2.4-5.7,3.8-9.2,3.8H6.5c-5.8,0-8.7-7-4.6-11.1L64.6,237.9z"/>
          <path fill="url(#solGrad2)" d="M64.6,3.8C67.1,1.4,70.4,0,73.8,0h317.4c5.8,0,8.7,7,4.6,11.1l-62.7,62.7c-2.4,2.4-5.7,3.8-9.2,3.8H6.5c-5.8,0-8.7-7-4.6-11.1L64.6,3.8z"/>
          <path fill="url(#solGrad3)" d="M333.1,120.1c-2.4-2.4-5.7-3.8-9.2-3.8H6.5c-5.8,0-8.7,7-4.6,11.1l62.7,62.7c2.4,2.4,5.7,3.8,9.2,3.8h317.4c5.8,0,8.7-7,4.6-11.1L333.1,120.1z"/>
        </svg>
      );
    case 'bnb':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2500 2500" style={svgStyle} className={className}>
          <path fill="#F3BA2F" d="M764.48 1050.52l288.02-288.02 288.02 288.02 167.52-167.52-455.54-455.54-455.54 455.54zm-344.04 193.98l167.52-167.52 167.52 167.52-167.52 167.52zm344.04 193.98l288.02 288.02 288.02-288.02 167.52 167.52-455.54 455.54-455.54-455.54zm631.54-193.98l167.52-167.52 167.52 167.52-167.52 167.52zm-343.54-111.98l-111.98 111.98-111.98-111.98 111.98-111.98z"/>
        </svg>
      );
    case 'doge':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 2000" style={svgStyle} className={className}>
          <g fill="#c2a633">
            <path d="M1024 659H881.12v281.69h224.79v117.94H881.12v281.67H1031c38.51 0 316.16 4.35 315.73-327.72S1077.44 659 1024 659z"/>
            <path d="M1000 0C447.71 0 0 447.71 0 1000s447.71 1000 1000 1000 1000-447.71 1000-1000S1552.29 0 1000 0zm39.29 1540.1H677.14v-481.46H549.48V940.7h127.65V459.21h310.82c73.53 0 560.56-15.27 560.56 549.48 0 574.09-509.21 531.41-509.21 531.41z"/>
          </g>
        </svg>
      );
    case 'xrp':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 424" style={svgStyle} className={className}>
          <path fill="#23292f" d="M437,0h74L357,152.48c-55.77,55.19-146.19,55.19-202,0L.94,0H75L192,115.83a91.11,91.11,0,0,0,127.91,0Z"/>
          <path fill="#23292f" d="M74.05,424H0L155,270.58c55.77-55.19,146.19,55.19,202,0L512,424H438L320,307.23a91.11,91.11,0,0,0-127.91,0Z"/>
        </svg>
      );
    default:
      return <span className={`font-bold ${className}`} style={{ fontSize: `${size}px` }}>{symbol.substring(0, 2)}</span>;
  }
}


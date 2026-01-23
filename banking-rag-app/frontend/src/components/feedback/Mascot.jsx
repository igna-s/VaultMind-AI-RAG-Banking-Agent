/**
 * Interactive Mascot
 * Uses Framer Motion to track mouse position for the eyes.
 * Reacts to 'password' type input focus by covering eyes.
 */
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export const Mascot = ({ isPasswordFocused }) => {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  
  useEffect(() => {
    const handleMouseMove = (e) => {
      // Calculate normalized position (-1 to 1)
      const x = (e.clientX / window.innerWidth) * 2 - 1;
      const y = (e.clientY / window.innerHeight) * 2 - 1;
      setMousePos({ x, y });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Eye movement logic
  const eyeVariant = {
    normal: { x: mousePos.x * 6, y: mousePos.y * 6 }, // Reduced range for more realism
    shy: { scale: 0.1, y: 10 }
  };
  
  // Hands animation variants
  const leftHandVariant = {
    hidden: { y: 120, x: -20, opacity: 0 },
    visible: { 
        y: 28, 
        x: 25, 
        opacity: 1,
        transition: { type: "spring", stiffness: 200, damping: 20 } 
    }
  };

  const rightHandVariant = {
    hidden: { y: 120, x: 20, opacity: 0 },
    visible: { 
        y: 28, 
        x: 75, 
        opacity: 1,
        transition: { type: "spring", stiffness: 200, damping: 20, delay: 0.05 } 
    }
  };

  return (
    <div className="relative w-40 h-40 mx-auto">
      {/* Face Container */}
      <svg viewBox="0 0 100 100" className="w-full h-full drop-shadow-2xl overflow-visible">
        <circle cx="50" cy="50" r="45" fill="#4f46e5" className="opacity-90" />
        
        {/* Eyes Container */}
        <motion.g animate={isPasswordFocused ? "shy" : "normal"}>
          {/* Left Eye Background */}
          <circle cx="35" cy="45" r="10" fill="white" />
          {/* Left Pupil */}
          <motion.circle 
            variants={eyeVariant}
            cx="35" cy="45" r="4" fill="#0f172a" 
          />
          
          {/* Right Eye Background */}
          <circle cx="65" cy="45" r="10" fill="white" />
          {/* Right Pupil */}
          <motion.circle 
            variants={eyeVariant}
            cx="65" cy="45" r="4" fill="#0f172a" 
          />
        </motion.g>

        {/* Mouth (Simple smile that fades when shy) */}
        <motion.path 
            d="M 35 65 Q 50 75 65 65" 
            fill="transparent" 
            stroke="white" 
            strokeWidth="3" 
            strokeLinecap="round"
            animate={{ opacity: isPasswordFocused ? 0 : 0.5 }}
        />

        {/* Hands Layer (Above Face) */}
        <motion.g initial="hidden" animate={isPasswordFocused ? "visible" : "hidden"}>
            {/* Left Hand */}
            <motion.circle variants={leftHandVariant} cx="0" cy="0" r="18" fill="#4f46e5" stroke="rgba(255,255,255,0.1)" strokeWidth="2" />
            {/* Right Hand */}
            <motion.circle variants={rightHandVariant} cx="0" cy="0" r="18" fill="#4f46e5" stroke="rgba(255,255,255,0.1)" strokeWidth="2" />
        </motion.g>
      </svg>
    </div>
  );
};

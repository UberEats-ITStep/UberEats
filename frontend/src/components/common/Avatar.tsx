import type { FC, ReactElement } from 'react';

type AvatarId = 'avatar_01' | 'avatar_02' | 'avatar_03' | 'avatar_04' | 'avatar_05' | 'avatar_06';

const DEFAULT_AVATAR: AvatarId = 'avatar_01';
const VALID_IDS: AvatarId[] = ['avatar_01', 'avatar_02', 'avatar_03', 'avatar_04', 'avatar_05', 'avatar_06'];

const GLYPHS: Record<AvatarId, ReactElement> = {
  avatar_01: <line x1="16" y1="32" x2="48" y2="32" className="stroke-text-primary" strokeWidth="2" />,
  avatar_02: (
    <g className="fill-text-primary">
      <circle cx="32" cy="22" r="2.5" />
      <circle cx="24" cy="38" r="2.5" />
      <circle cx="40" cy="38" r="2.5" />
    </g>
  ),
  avatar_03: <rect x="20" y="20" width="24" height="24" className="stroke-text-primary" strokeWidth="2" fill="none" />,
  avatar_04: (
    <g className="fill-text-primary">
      {[18, 32, 46].flatMap((cx) =>
        [18, 32, 46].map((cy) => <circle key={`${cx}-${cy}`} cx={cx} cy={cy} r="1.75" />)
      )}
    </g>
  ),
  avatar_05: (
    <path
      d="M36 18v28M28 18v14a7 7 0 0 0 8 0"
      className="stroke-text-primary"
      strokeWidth="2"
      fill="none"
      strokeLinecap="square"
    />
  ),
  avatar_06: <path d="M18 46a28 28 0 0 1 28-28" className="stroke-text-primary" strokeWidth="2" fill="none" />,
};

export interface AvatarProps {
  avatarId?: string | null;
  name?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeClasses = { sm: 'w-8 h-8', md: 'w-12 h-12', lg: 'w-16 h-16' };

export const Avatar: FC<AvatarProps> = ({ avatarId, name, size = 'md', className = '' }) => {
  const resolvedId = VALID_IDS.includes(avatarId as AvatarId) ? (avatarId as AvatarId) : DEFAULT_AVATAR;

  return (
    <svg
      viewBox="0 0 64 64"
      className={`${sizeClasses[size]} shrink-0 ${className}`}
      role="img"
      aria-label={name ? `${name}'s avatar` : 'User avatar'}
    >
      <rect x="1.5" y="1.5" width="61" height="61" className="fill-surface stroke-border-default" strokeWidth="1.5" />
      {GLYPHS[resolvedId]}
      <rect x="52" y="4" width="8" height="8" className="fill-accent" />
    </svg>
  );
};

export default Avatar;

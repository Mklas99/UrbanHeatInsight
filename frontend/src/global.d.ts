declare module '*.css' {
  const classes: { [key: string]: string };
  export default classes;
}
// Type declarations for static assets
declare module '*.png' {
  const content: string;
  export default content;
}

declare module '*.jpg' {
  const content: string;
  export default content;
}

declare module '*.svg' {
  const content: string;
  export default content;
}
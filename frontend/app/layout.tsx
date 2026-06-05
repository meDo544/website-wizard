import "./globals.css";

export const metadata = {
  title: "Website Wizard",
  description: "AI Website Generator",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}

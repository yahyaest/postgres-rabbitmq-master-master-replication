import { PrimeReactProvider } from 'primereact/api';
import './globals.css'
import "primereact/resources/themes/lara-light-indigo/theme.css";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <PrimeReactProvider>
    <html lang="en">
      <body>{children}</body>
    </html>
    </PrimeReactProvider>
  )
}

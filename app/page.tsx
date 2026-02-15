import Nav from '@/components/Nav'
import Hero from '@/components/Hero'
import HowItWorks from '@/components/HowItWorks'
import Tools from '@/components/Tools'
import Marketplace from '@/components/Marketplace'
import AgentChat from '@/components/AgentChat'
import Dashboard from '@/components/Dashboard'
import Footer from '@/components/Footer'

export default function Home() {
  return (
    <>
      <Nav />
      <Hero />
      <HowItWorks />
      <Tools />
      <Marketplace />
      <AgentChat />
      <Dashboard />
      <Footer />
    </>
  )
}

"use client"
import Header from "@/app/_components/header"
import HeroContent from "@/app/_components/hero-content"
import PulsingCircle from "@/app/_components/pulsing-circle"
import ShaderBackground from "@/app/_components/shader-background"

export default async function home() {
    return (
        <div>
            <ShaderBackground>
            <Header />
            <HeroContent />
            <PulsingCircle />
            </ShaderBackground>
        </div>
    )
}
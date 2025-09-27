import { auth } from "@/server/auth";
import { redirect } from "next/navigation";
import dynamic from "next/dynamic"
import { Suspense } from "react"
import SearchInterface from "@/app/_components/interactive/SearchInterface"
import ResultsLayout from "../_components/interactive/visualizations";

const Globe = dynamic(() => import("@/app/_components/interactive/globe"))
// {ssr: false}

export default async function AppPage() {
  const session = await auth();
  if (!session) {
    redirect("/");
  }

  return (
     <div className="relative min-h-screen bg-black overflow-hidden">
              <h1>Welcome to the App</h1>
              <p>You’re logged in as {session.user?.email}</p>
     <Suspense fallback={<div>Loading...</div>}>
       <ResultsLayout></ResultsLayout>
     </Suspense>
     <SearchInterface />
   </div>
  );
}

import { getAllPosts, getAllTags } from '@/lib/notion'
import SearchLayout from '@/layouts/search'

export default function search({ tags, posts }) {
  return <SearchLayout tags={tags} posts={posts} />
}
export async function getStaticProps() {
  let posts = await getAllPosts()
  posts = posts.filter(
    post => post.status[0].toLowerCase() === 'published' && post.type[0].toLowerCase() === 'post'
  )
  const tags = await getAllTags()
  return {
    props: {
      tags,
      posts
    },
    revalidate: 1
  }
}

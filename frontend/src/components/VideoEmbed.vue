<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(defineProps<{ url: string; title?: string }>(), {
	title: "Exercise video",
});

type Embed = { type: "iframe" | "video" | "link"; src: string };

const YOUTUBE_HOSTS = ["youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"];
const VIMEO_HOSTS = ["vimeo.com", "www.vimeo.com", "player.vimeo.com"];
const VIDEO_FILE = /\.(mp4|webm|ogg)$/i;

const embed = computed<Embed | null>(() => {
	let parsed: URL;
	try {
		parsed = new URL(props.url.trim());
	} catch {
		return null;
	}
	if (parsed.protocol !== "http:" && parsed.protocol !== "https:") return null;

	const host = parsed.hostname.toLowerCase();

	if (YOUTUBE_HOSTS.includes(host)) {
		const id = youTubeId(parsed);
		if (id) return { type: "iframe", src: `https://www.youtube-nocookie.com/embed/${id}` };
	}

	if (VIMEO_HOSTS.includes(host)) {
		const id = parsed.pathname.split("/").filter(Boolean).pop();
		if (id && /^\d+$/.test(id))
			return { type: "iframe", src: `https://player.vimeo.com/video/${id}` };
	}

	if (VIDEO_FILE.test(parsed.pathname)) return { type: "video", src: parsed.href };

	return { type: "link", src: parsed.href };
});

function youTubeId(parsed: URL): string | null {
	if (parsed.hostname.toLowerCase() === "youtu.be") {
		return parsed.pathname.split("/").filter(Boolean)[0] ?? null;
	}
	const [, kind, id] = parsed.pathname.split("/");
	if (kind === "embed" || kind === "shorts") return id ?? null;
	return parsed.searchParams.get("v");
}
</script>

<template>
	<div v-if="embed">
		<div
			v-if="embed.type === 'iframe'"
			class="aspect-video w-full overflow-hidden rounded-[18px] bg-black"
		>
			<iframe
				class="size-full"
				:src="embed.src"
				:title="title"
				loading="lazy"
				allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
				referrerpolicy="strict-origin-when-cross-origin"
				allowfullscreen
			/>
		</div>

		<video
			v-else-if="embed.type === 'video'"
			:src="embed.src"
			controls
			preload="metadata"
			class="w-full rounded-[18px] bg-black"
		/>

		<a
			v-else
			:href="embed.src"
			target="_blank"
			rel="noopener noreferrer"
			class="inline-flex items-center gap-2 text-sm-semibold text-ink-gray-9 underline-offset-4 hover:underline"
		>
			<span class="lucide-circle-play size-4" />
			Watch the demo
		</a>
	</div>
</template>

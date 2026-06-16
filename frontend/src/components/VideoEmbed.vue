<template>
	<!-- Nothing renders unless we have a usable, parseable URL. -->
	<div v-if="embed" class="w-full">
		<!-- YouTube / Vimeo: sandboxed iframe -->
		<div
			v-if="embed.type === 'iframe'"
			class="relative w-full overflow-hidden rounded-xl bg-black"
			:style="{ aspectRatio: '16 / 9' }"
		>
			<iframe
				width="560"
				height="315"
				:src="embed.src"
				:title="title"
				frameborder="0"
				allow="
					accelerometer;
					autoplay;
					clipboard-write;
					encrypted-media;
					gyroscope;
					picture-in-picture;
					web-share;
				"
				referrerpolicy="strict-origin-when-cross-origin"
				allowfullscreen
			></iframe>
		</div>

		<!-- Direct video file -->
		<video
			v-else-if="embed.type === 'video'"
			:src="embed.src"
			controls
			preload="metadata"
			class="w-full rounded-xl bg-black"
		></video>

		<!-- Unknown host: never iframe arbitrary URLs — link out instead -->
		<a
			v-else
			:href="embed.src"
			target="_blank"
			rel="noopener noreferrer"
			class="inline-flex items-center gap-2 text-sm font-medium text-ink-blue-3 hover:underline"
		>
			<FeatherIcon name="play-circle" class="h-4 w-4" />
			Watch video
		</a>
	</div>
</template>

<script setup>
import { computed } from "vue";
import { FeatherIcon } from "frappe-ui";

const props = defineProps({
	url: { type: String, default: "" },
	title: { type: String, default: "Exercise video" },
});

const YOUTUBE_HOSTS = ["youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"];
const VIMEO_HOSTS = ["vimeo.com", "www.vimeo.com", "player.vimeo.com"];
const VIDEO_FILE = /\.(mp4|webm|ogg)(\?.*)?$/i;

/**
 * Turn a raw URL into a safe, embeddable descriptor, or null if it isn't
 * usable. Only http(s) is allowed, so javascript:/data: URLs can never embed.
 */
const embed = computed(() => {
	const raw = (props.url || "").trim();
	if (!raw) return null;

	let parsed;
	try {
		parsed = new URL(raw);
	} catch {
		return null;
	}

	if (parsed.protocol !== "http:" && parsed.protocol !== "https:") return null;

	const host = parsed.hostname.toLowerCase();

	if (YOUTUBE_HOSTS.includes(host)) {
		const id = youTubeId(parsed);
		if (id) return { type: "iframe", src: `https://www.youtube.com/embed/${id}` };
	}

	if (VIMEO_HOSTS.includes(host)) {
		const id = parsed.pathname.split("/").filter(Boolean).pop();
		if (id && /^\d+$/.test(id)) {
			return { type: "iframe", src: `https://player.vimeo.com/video/${id}` };
		}
	}

	if (VIDEO_FILE.test(parsed.pathname)) return { type: "video", src: parsed.href };

	// Recognised as a real link but not embeddable — offer it as a link.
	return { type: "link", src: parsed.href };
});

function youTubeId(parsed) {
	if (parsed.hostname.toLowerCase() === "youtu.be") {
		return parsed.pathname.split("/").filter(Boolean)[0] || null;
	}
	if (parsed.pathname.startsWith("/embed/")) {
		return parsed.pathname.split("/")[2] || null;
	}
	return parsed.searchParams.get("v");
}
</script>

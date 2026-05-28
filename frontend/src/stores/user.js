import { createResource } from 'frappe-ui'
import { defineStore } from 'pinia'
import { ref, toRaw, watch } from 'vue'

export const useUserStore = defineStore('user', () => {
	const user = ref(null)

	const fetchUserResource = createResource({
		url: 'zoezy.api.user.get_user_details',
		auto: true,
		onSuccess: (data) => {
			user.value = data
		},
	})

	return { user, fetchUserResource }
})

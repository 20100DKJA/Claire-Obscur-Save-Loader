import os

from clair_obscur_save_loader.managers.profile import ProfileManager


class TestProfileManager:
    def test_get_profiles_list(self, profile_manager: ProfileManager) -> None:
        profiles = profile_manager.get_list_of_profiles()

        # Vérifier le contenu de la liste
        assert len(profiles) == 3
        assert 'default' in profiles
        assert 'other' in profiles

    def test_create_profile(self, profile_manager: ProfileManager) -> None:
        profile_manager.create('new_profile')
        assert os.path.exists(os.path.join(profile_manager.profiles_save_path, 'new_profile'))

    def test_delete_profile(self, profile_manager: ProfileManager) -> None:
        try:
            profile_manager.delete('other')

            assert not os.path.exists(os.path.join(profile_manager.profiles_save_path, 'other'))
        except PermissionError:
            pass

    def test_rename_profile(self, profile_manager: ProfileManager) -> None:
        profile_manager.rename('default', 'new_name')

        assert os.path.exists(os.path.join(profile_manager.profiles_save_path, 'new_name'))
        assert not os.path.exists(os.path.join(profile_manager.profiles_save_path, 'default'))

    def test_duplicate_profile(self, profile_manager: ProfileManager) -> None:
        profile_manager.duplicate('default', 'new_default')

        assert os.path.exists(os.path.join(profile_manager.profiles_save_path, 'new_default'))
        assert os.path.exists(os.path.join(profile_manager.profiles_save_path, 'default'))

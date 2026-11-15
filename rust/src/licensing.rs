use sha2::{Digest, Sha256};
use subtle::ConstantTimeEq;

const ORIGINAL_KEY_HASH: &str = "c052eb83528666dfb18df5d39cf6ab1c3058bb7b5720135a1012b5a3ba093042";

pub fn hashed_product_key(candidate: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(candidate.to_uppercase().as_bytes());
    hex::encode(hasher.finalize())
}

pub fn valid_product_key(candidate: &str) -> bool {
    let hashed = hashed_product_key(candidate);
    hashed.as_bytes().ct_eq(ORIGINAL_KEY_HASH.as_bytes()).into()
}

#[cfg(windows)]
pub fn is_activated() -> bool {
    use winreg::{enums::HKEY_CURRENT_USER, RegKey};
    let hkcu = RegKey::predef(HKEY_CURRENT_USER);
    hkcu.open_subkey("Software\\InMan")
        .and_then(|key| key.get_value::<String, _>("ProductKey"))
        .map(|hash| hash.as_bytes().ct_eq(ORIGINAL_KEY_HASH.as_bytes()).into())
        .unwrap_or(false)
}

#[cfg(not(windows))]
pub fn is_activated() -> bool { false }

#[cfg(windows)]
pub fn activate(candidate: &str) -> anyhow::Result<()> {
    use winreg::{enums::HKEY_CURRENT_USER, RegKey};
    anyhow::ensure!(valid_product_key(candidate), "Invalid Product Key");
    let hkcu = RegKey::predef(HKEY_CURRENT_USER);
    let (registry, _) = hkcu.create_subkey("Software\\InMan")?;
    registry.set_value("ProductKey", &hashed_product_key(candidate))?;
    Ok(())
}

#[cfg(not(windows))]
pub fn activate(_: &str) -> anyhow::Result<()> {
    anyhow::bail!("Activation is supported on Windows only")
}

/// Matches controllers/auth.py: 16 random salt bytes plus SHA256(salt || password).
pub fn hash_password(password: &str) -> anyhow::Result<String> {
    let mut salt = [0_u8;16];
    getrandom::fill(&mut salt).map_err(|error| anyhow::anyhow!(
        "Unable to generate a secure password salt: {error}"
    ))?;
    let mut hasher = Sha256::new();
    hasher.update(salt);
    hasher.update(password.as_bytes());
    Ok(format!("{}:{}",hex::encode(salt),hex::encode(hasher.finalize())))
}

/// Python compatibility: os.urandom(16), SHA256(salt || password), hex salt:hex digest.
pub fn verify_password(password: &str, stored: &str) -> bool {
    let Some((salt_hex, digest_hex)) = stored.split_once(':') else { return false };
    let Ok(salt) = hex::decode(salt_hex) else { return false };
    let Ok(expected) = hex::decode(digest_hex) else { return false };
    if salt.len() != 16 || expected.len() != 32 { return false; }
    let mut hasher = Sha256::new();
    hasher.update(&salt);
    hasher.update(password.as_bytes());
    let digest = hasher.finalize();
    digest.as_slice().ct_eq(expected.as_slice()).into()
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn key_normalization_matches_original_python() {
        assert_eq!(hashed_product_key("AbC"), hashed_product_key("ABC"));
        assert!(!valid_product_key("incorrect"));
    }
    #[test]
    fn malformed_password_hashes_are_rejected() {
        assert!(!verify_password("p", ""));
        assert!(!verify_password("p", "not-hex:abc"));
        assert!(!verify_password("p", "1234:5678"));
    }
    #[test]
    fn python_salted_hash_is_accepted() {
        let salt = [0xAB; 16];
        let mut h = Sha256::new();
        h.update(salt);
        h.update(b"correct");
        let stored = format!("{}:{}", hex::encode(salt), hex::encode(h.finalize()));
        assert!(verify_password("correct", &stored));
        assert!(!verify_password("incorrect", &stored));
    }
}
